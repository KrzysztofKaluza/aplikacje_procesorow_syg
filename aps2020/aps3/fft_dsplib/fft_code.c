#define _USE_MATH_DEFINES
#include <stdio.h>
#include <math.h>


#define N_FFT 512
#define N2 1024

__declspec(dllexport) void bit_rev(float* x, int n); 
__declspec(dllexport) void tw_genr2fft(float* w, int n);
__declspec(dllexport) void DSPF_sp_cfftr2_dit(float     * x, float * w, int n);
__declspec(dllexport) void modul(float * x, int n);

#include "DSPF_sp_cfftr2_dit.c"
#include "utility.c"

int N;
float x[N2];
float w[N_FFT];

int main(){
    N = N_FFT;
    for(short i=0; i<N; i++){
        x[2*i] = sin(2*M_PI*i/N);
        x[2*i+1] = 0;
    }
    tw_genr2fft(w, N);
    bit_rev(w, N>>1);
    DSPF_sp_cfftr2_dit(x, w, N);
    bit_rev(x, N);
    modul(x, N);
    return 0;
}

void modul(float * x, int n){
    int i;
    for(i=0 ; i<n ; i++){
        x[i]=sqrt( (x[2*i] * x[2*i]) + (x[2*i+1] * x[2*i+1]) );
    }
}