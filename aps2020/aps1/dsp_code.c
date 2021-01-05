#include <math.h>
#include <stdio.h>

__declspec(dllexport) int sampleProcessor(int input_adc);

int main()
{
    // test case 1
    const test_val = 5;
    int output_sample = sampleProcessor(test_val);
    printf("sample after processing: %d", output_sample);
    return 0;
}

__declspec(dllexport) int sampleProcessor(int input_adc)
{
    return input_adc/2;
}

