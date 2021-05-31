package com.example.eq;

import java.io.*;

public class SolveEquation
{
    // Function to solve
// the given equation
    static String solveEquation(String equation)
    {
        int n = equation.length(),
                sign = 1, coeff = 0;
        int total = 0, i = 0;

        // Traverse the equation
        for (int j = 0; j < n; j++)
        {
            if (equation.charAt(j) == '+' ||
                    equation.charAt(j) == '-')
            {
                if (j > i)
                    total += sign *
                            Integer.parseInt(
                                    equation.substring(i, j));
                i = j;
            }

            // For cases such
            // as: x, -x, +x
            else if (equation.charAt(j) == 'x')
            {
                if ((i == j) ||
                        equation.charAt(j - 1) == '+')
                    coeff += sign;

                else if (equation.charAt(j - 1) == '-')
                    coeff -= sign;

                else
                    coeff += sign *
                            Integer.parseInt(
                                    equation.substring(i, j));
                i = j + 1;
            }

            // Flip sign once
            // '=' is seen
            else if (equation.charAt(j) == '=')
            {
                if (j > i)
                    total += sign *
                            Integer.parseInt(
                                    equation.substring(i, j));
                sign = -1;
                i = j + 1;
            }
        }

        // There may be a
        // number left in the end
        if (i < n)
            total = total +
                    sign *
                            Integer.parseInt(
                                    equation.substring(i));

        // For infinite
        // solutions
        if (coeff == 0 &&
                total == 0)
            return "Infinite solutions";

        // For no solution
        if (coeff == 0 &&
                total != 0)
            return "No solution";

        // x = total sum / coeff
        // of x '-' sign indicates
        // moving numeric value to
        // right hand side
        int ans = -total / coeff;
        return (Integer.toString(ans));
    }
}
