from ctypes as ct

lib = ct.cdll.LoadLibrary('C:/aps2020/aps1/dsp_code.dll')
data_in = 1
while data_in != '999':
    data_in = input('Wprowadz liczbe: ')
    int_data_in = int(data_in)
    data_out_c = lib.sampleProcessor(int_data_in)
    data_out_p = int_data_in//2
    print('Wynik procedury jezyka C:; ', data_out_c)
    print('Wynik procedury w Pythonie: ', data_out_p)
