#define _USE_MATH_DEFINES
#include <math.h>
#include <stdio.h>

#include "utility.c"
#include "DSPF_sp_cfftr2_dit.c"


#define N_FFT 512

__declspec(dllexport) int n;

float w[N_FFT];

__declspec(dllexport) int probki[N_FFT];
__declspec(dllexport) float mx[N_FFT];
float x[2*N_FFT];


void modul(float * x, int n){
    int i;
    for(i=0 ; i<n ; i++){
        mx[i]=sqrt( (x[2*i] * x[2*i]) + (x[2*i+1] * x[2*i+1]) );
    }
}

__declspec(dllexport) void init_fft(){
    n = 0;
    for(short i=0; i<N_FFT; i++){
        probki[i] = sin(2*M_PI*i/N_FFT);
    }
    tw_genr2fft(w, N_FFT);
    bit_rev(w, N_FFT >> 1);
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
        DSPF_sp_cfftr2_dit(x, w, N_FFT);
        bit_rev(x, N_FFT);
        modul(x, N_FFT);
    }
    return input_adc/2;
}

int main(){
    init_fft();
    int a = sampleProcessor(4);
    return 0;
}
