#define _USE_MATH_DEFINES
#include <math.h>
#include <stdio.h>
#include "utility.c"
#include "DSPF_sp_cfftr2_dit.c"

#define N_FFT 512

__declspec(dllexport) int n;

float w[N_FFT];

float hamming_window[N_FFT];
float hanning_window[N_FFT];

__declspec(dllexport) int probki[N_FFT];
__declspec(dllexport) float mx[N_FFT];
__declspec(dllexport) float mxhm[N_FFT];
__declspec(dllexport) float mxhn[N_FFT];
__declspec(dllexport) float xhm[2*N_FFT];
__declspec(dllexport) float xhn[2*N_FFT];
float x[2*N_FFT];

void modul(float * mx, float * x, int N){
    int i;
    for(i=0 ; i<N ; i++){
        mx[i] = sqrt( (x[2*i] * x[2*i]) + (x[2*i+1] * x[2*i+1]) )/(0.5*N);   
    }
}

void window_hamming(int n)
{
    int i;
	for( i=0;i<n;++i)
	{
		hamming_window[i]=(0.53836 - 0.46164 * cos((2*PI*i) / (N_FFT)));
	}
}

void window_hanning(int n)
{
   int i;
	for( i=0;i<n;++i)
	{
		hanning_window[i]=(1- cos((2*PI*i)/(N_FFT)));
	}
}

__declspec(dllexport) void init_fft(){
    n = 0;
    for(short i=0; i<N_FFT; i++){
        probki[i] = sin(2*M_PI*i/N_FFT);
    }
    tw_genr2fft(w, N_FFT);
    bit_rev(w, N_FFT >> 1);
    window_hamming(N_FFT);
    window_hanning(N_FFT);
}



__declspec(dllexport) int sampleProcessor(int input_adc){ 
    probki[n] = input_adc;
    x[2*n] = input_adc;
    x[2*n+1] = 0;
    n++; 
    if(n>511){
        n = 0;
    }
    if(n == 0){
        
        for(int i = 0; i<N_FFT;i++){
            xhm[i*2] = hamming_window[i]*x[i*2];
            xhm[i*2+1] = 0;
            xhn[i*2] = hanning_window[i]*x[i*2];
            xhn[i*2+1] = 0;
        }

        DSPF_sp_cfftr2_dit(xhm, w, N_FFT);
        bit_rev(xhm, N_FFT);
        modul(mxhm, xhm, N_FFT);
        
        DSPF_sp_cfftr2_dit(xhn, w, N_FFT);
        bit_rev(xhn, N_FFT);
        modul(mxhn ,xhn, N_FFT);

        DSPF_sp_cfftr2_dit(x, w, N_FFT);
        bit_rev(x, N_FFT);
        modul(mx, x, N_FFT);
    }
    return input_adc/2;
}
int main(){

    return 0;
}