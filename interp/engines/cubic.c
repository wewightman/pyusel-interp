#include "cubic.h"
#include <stdint.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/**
 * cubic1D_fixed: 1D cubic interpolator for a fixed sampling scheme
 * Based on the cubic interpolation algorithm from Numerical Recipes
 * Comments are to the writer's knowledge
 * Wren Wightman, github:@wewightman, 2023
 * 
 * Parameters:
 *  xin:    pointer to vector of intperpolation coordinates
 *  Nin:    number of input coordinates
 *  knots:  knot structure with interpolation parameters
*/
float * cubic1D_fixed(float ** pxin, int Nin, IntrpData1D_Fixed ** pknots) 
{
    // loop variables and return buffer
    float x, a, b, c, d, xlead, xlag;
    int j;

    // derefernce pointer-to-pointers
    IntrpData1D_Fixed * knots = *pknots;
    float * xin = *pxin;

    float * y = (float *) malloc(sizeof(float) * Nin);

    // procedurally define bounds
    float dx = knots->dx;
    float xmin = knots->xstart;
    float xmax = xmin + dx * (float)((knots->N) - 1);

    for(int i=0; i<Nin; ++i) 
    {
        x = xin[i];         // extract interpolation point
        j = (int) (x/dx);   // calculate knot index

        // if out of bounds, return fill vlaue
        if ((j < 0) || (j >= ((knots->N) - 1)))
        {
            y[i] = knots->fill;
        }

        // interpolate in bounds
        else
        {
            // extract x value
            xlead = xmin + dx * (int)(j+1); // calculate high x
            xlag = xmin + dx * (int)(j);    // calculate low x

            // generate interpolation terms
            a = (xlead - x) / dx;
            b = (x - xlag) / dx;
            c = (1.0f/6.0f) * (powf(a, 3.0f) - a) * powf(dx, 1.0f);
            d = (1.0f/6.0f) * (powf(b, 3.0f) - b) * powf(dx, 2.0f);

            // calculate y value
            y[i] = a*(knots->y)[j] + b*knots->y[j+1] + c*knots->y2[j] + d*knots->y2[j+1];
        }
    }
    return y;
}


/**
 * tie_knots1D_fixed: Generate second-derivative knots for a fixed sampling scheme
 * Based on the cubic interpolation algorithm from Numerical Recipes
 * Comments are to the writer's knowledge
 * Wren Wightman, github:@wewightman, 2023
*/
IntrpData1D_Fixed * tie_knots1D_fixed(float ** py, int N, float dx, float xstart, float fill) {
    // generate loop variables and buffers
    float * y2 = (float *) malloc(sizeof(float) * N);
    float * u  = (float *) malloc(sizeof(float) * N);

    float *y = *py;

    // set y'' = 0 boundary condition
    y2[0] = 0.0f;
    u[0] = 0.0f;

    // forward decomposition loop of tri-diagonal inversion algorithm
    for (int i=0; i < N-1; ++i)
    {
        y2[i] = 0.0f;
        u[i] = (y[i+1] - y[i])/dx - (y[i] - y[i-1])/dx;
        u[i] = (6.0f*u[i] / (2.0f*dx) - u[i-1]) / (y2[i-1] + 2.0f);
    }

    // backsubstitution loop of tridiagonal algorithm
    y2[N-1] = 0.0f;

    for (int k = N-2; k >= 0; k--) 
    {
        y2[k] = y2[k] * y2[k+1] + u[k];
    }

    free(u); // free loop buffer

    // return a filled knots structure
    IntrpData1D_Fixed * knots = (IntrpData1D_Fixed *) malloc(sizeof(IntrpData1D_Fixed));
    knots->dx = dx;
    knots->xstart = xstart;
    knots->N = N;
    knots->y = y;
    knots->fill = fill;
    knots->y2 = y2;

    return knots;
}
