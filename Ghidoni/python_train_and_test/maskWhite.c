#include <time.h>
#include <stdlib.h>
#include <stdio.h>
__declspec(dllexport) void __cdecl applyDamageMask(const void* qr, const void* mask, void* qr_damaged, const int h, const int w) {


	//srand(time(NULL));
	for (int i = 0; i < h; i++) {
		for (int j = 0; j < w; j++) {
			//printf("%d ", ((int*)mask)[i * w * 3 + j * 3 + 0]);
			if (((int*)mask)[i * w * 3 + j * 3 + 0] == 0 &&
				((int*)mask)[i * w * 3 + j * 3 + 1] == 0 &&
				((int*)mask)[i * w * 3 + j * 3 + 2] == 0) {

				/*((int*)qr_damaged)[i * w * 3 + j * 3 + 0] = rand() % 256;
				((int*)qr_damaged)[i * w * 3 + j * 3 + 1] = rand() % 256;
				((int*)qr_damaged)[i * w * 3 + j * 3 + 2] = rand() % 256;*/
				((int*)qr_damaged)[i * w * 3 + j * 3 + 0] = 255;
				((int*)qr_damaged)[i * w * 3 + j * 3 + 1] = 255;
				((int*)qr_damaged)[i * w * 3 + j * 3 + 2] = 255;
			}
			else {
				((int*)qr_damaged)[i * w * 3 + j * 3 + 0] = ((int*)qr)[i * w + j];
				((int*)qr_damaged)[i * w * 3 + j * 3 + 1] = ((int*)qr)[i * w + j];
				((int*)qr_damaged)[i * w * 3 + j * 3 + 2] = ((int*)qr)[i * w + j];



			}
		}
		//printf('\n');
	}
}