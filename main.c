#include <stdio.h>
#include <math.h>
#include "cubic.h"

int main(int argc, char *argv[]) {
    float * y1 = malloc(sizeof(float)*16);
    float * x2 = malloc(sizeof(float)*64);
    float dx = 1.0f;

    for(int i=0; i<64; ++i)
    {
        float i_f = (float) i;
        x2[i] = i_f * dx / 5.0f - 1.0;
    }

    float frac;

    printf("y1\n");
    for(int i=0; i < 16; i++)
    {
        frac = (float) i;
        frac /= 15.0f;
        y1[i] = sinf(6.28318530718f * frac);
        printf("  %0.05f\n", y1[i]);
    }

    IntrpData1D_Fixed * knots;
    knots = tie_knots1D_fixed(y1, 16, dx, 0.0f, 3.0f);
    float * y2 = cubic1D_fixed(x2, 64, knots);

    printf("y2\n");
    for(int i=0; i < 64; i++)
    {
        printf("  %0.05f\n", y2[i]);
    }
}