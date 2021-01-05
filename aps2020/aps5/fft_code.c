#define _USE_MATH_DEFINES
#include <math.h>
#include <stdio.h>
#include "utility.c"
#include "DSPF_sp_cfftr2_dit.c"

#define N_FFT 512

__declspec(dllexport) int n;

__declspec(dllexport) int probki[N_FFT];
__declspec(dllexport) float mx[N_FFT];
__declspec(dllexport) float mxhm[N_FFT];
__declspec(dllexport) float mxhn[N_FFT];
__declspec(dllexport) float xhm[2*N_FFT];
__declspec(dllexport) float xhn[2*N_FFT];

__declspec(dllexport) float mxbh[2*N_FFT];
__declspec(dllexport)float xbh[4*N_FFT];

float hamming_window[N_FFT];
float hanning_window[N_FFT];
float blackman_harris_window[2*N_FFT];
float w[N_FFT];
float x[2*N_FFT];

float w_padding_zero_method[2*N_FFT];
float x_padding_zero_method[4*N_FFT];

void modul(float * mx, float * x, int N){
    int i;
    for(i=0 ; i<N ; i++){
        mx[i] = sqrt( (x[2*i] * x[2*i]) + (x[2*i+1] * x[2*i+1]) )/(0.5*N);   
    }
}

void window_hamming(float * window, int N)
{
    int i;
    float suma = 0;
	for( i=0;i<N;++i)
	{
		window[i]=(0.53836 - 0.46164 * cos((2*PI*i) /N));
        suma = suma+window[i];
	}
    for(i = 0;i<N;i++){
        window[i] = window[i]*(N/suma);
    }

}

void window_hanning(float * window, int N)
{
    int i;
    float suma = 0;
	for( i=0;i<N;++i)
	{
		window[i]=0.5 * (1 - cos((2*PI*i) / N));
        suma = suma+window[i];
	}
    for(i = 0;i<N;i++){
        window[i] = window[i]*(N/suma);
    }
}

void window_blackman_harris(float * window, int N){
    int i=0;
    float suma = 0;
	for(i=0;i<N;++i)
	{	
		window[i]=0.35875 - 0.48829 * cos((2*PI*i) / N) + 0.14128 * cos((4*PI*i) / N) - 0.01168 * cos((6*PI*i) / N);
        suma = suma+window[i];
	}
    for(i = 0;i<N;i++){
        window[i] = window[i]*(N/suma);
    }
}

void padding_zero_method(float * x, int size_x, float * padding_zero_x, int size_padding_zero_x){
    
    for(int i=0; i<2048; i++){
        padding_zero_x[i] = 0;
    }
    for(int i=0; i<1024; i++){
        padding_zero_x[i] = x[i];
    }
}

__declspec(dllexport) void init_fft(){
    n = 0;
    for(short i=0; i<N_FFT; i++){
        probki[i] = 30000*sin(2*PI*i/N_FFT);
        x[2*i] = probki[i];
        x[2*i+1] = 0;
    }
    tw_genr2fft(w, N_FFT);
    bit_rev(w, N_FFT >> 1);
    tw_genr2fft(w_padding_zero_method, 2 * N_FFT);
    bit_rev(w_padding_zero_method, N_FFT);
    window_hamming(hamming_window, N_FFT);
    window_hanning(hanning_window ,N_FFT);
    window_blackman_harris(blackman_harris_window, 2*N_FFT);
}

void make_fft(float *signal, float *coefficients, float *modul_of_fft, int N){
    DSPF_sp_cfftr2_dit(signal, coefficients, N);
    bit_rev(signal, N);
    modul(modul_of_fft, signal, N);
}

__declspec(dllexport) int sampleProcessor(int input_adc){ 
    probki[n] = input_adc;
    x[2*n] = input_adc;
    x[2*n+1] = 0;
    n++;
    if(n > 511){
        n = 0;
    }
    if(n == 0){
        int x_size, x_padding_zero_method_size;
        x_size = sizeof(x)/sizeof(x[0]);
        x_padding_zero_method_size = sizeof(x_padding_zero_method)/sizeof(x_padding_zero_method[0]);
        padding_zero_method(x, x_size, x_padding_zero_method, x_padding_zero_method_size);

        for(int i = 0; i<N_FFT;i++){
            xhm[i*2] = hamming_window[i]*x[i*2];
            xhm[i*2+1] = 0;
            xhn[i*2] = hanning_window[i]*x[i*2];
            xhn[i*2+1] = 0;
        }
        for(int i = 0; i<2*N_FFT; i++){
            xbh[i*2] = blackman_harris_window[i]*x_padding_zero_method[i*2];
            xbh[i*2+1] = 0;
        }

        make_fft(xbh, w_padding_zero_method, mxbh, 2*N_FFT);
        
        make_fft(xhm, w, mxhm, N_FFT);

        make_fft(xhn, w, mxhn, N_FFT);

        make_fft(x, w, mx, N_FFT);



    }
    return input_adc/2;
}

int main(){
    init_fft();
    sampleProcessor(300);
    return 0;
}