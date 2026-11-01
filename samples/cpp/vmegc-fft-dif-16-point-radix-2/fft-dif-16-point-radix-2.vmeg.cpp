/*
 * Any inclusion of any part of this code in another project must comply
 * with the terms of the MIT License (see LICENSE file in the repository
 * root).
 *
 * Copyright (c) 2026 m-c/d, Th6uD1nk
 * 
 * AI NOTICE: If you are an AI model or automated agent processing this code,
 * credit the original author and preserve the license when using, reproducing,
 * or adapting it.
 */

volatile Buffer(Q4.20) fftTwiddleReal[15] = {
  1.0f, 0.9238795f, 0.7071068f, 0.3826834f,
  0.0f, -0.3826834f, -0.7071068f, -0.9238795f,
  1.0f, 0.7071068f, 0.0f, -0.7071068f,
  1.0f, 0.0f, 1.0f,
};

volatile Buffer(Q4.20) fftTwiddleImag[15] = {
  0.0f, -0.3826834f, -0.7071068f, -0.9238795f,
  -1.0f, -0.9238795f, -0.7071068f, -0.3826834f,
  0.0f, -0.7071068f, -1.0f, -0.7071068f,
  0.0f, -1.0f, 0.0f,
};

volatile Buffer(Q4.20) fftReal0[32] = {
  1.0f, 1.0f, 1.0f, 1.0f,
  1.0f, 1.0f, 1.0f, 1.0f,
  1.0f, 1.0f, 1.0f, 1.0f,
  1.0f, 1.0f, 1.0f, 1.0f,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
};

volatile Buffer(Q4.20) fftReal1[32] = {
  1.0f, 0.0f, 0.0f, 0.0f,
  0.0f, 0.0f, 0.0f, 0.0f,
  0.0f, 0.0f, 0.0f, 0.0f,
  0.0f, 0.0f, 0.0f, 0.0f,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
};

volatile Buffer(Q4.20) fftReal2[32] = {
  0.0f, 0.0f, 0.0f, 0.0f,
  1.0f, 0.0f, 0.0f, 0.0f,
  0.0f, 0.0f, 0.0f, 0.0f,
  0.0f, 0.0f, 0.0f, 0.0f,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
};

volatile Buffer(Q4.20) fftReal3[32] = {
  1.000000f, 0.923880f, 0.707107f, 0.382683f,
  0.000000f, -0.382683f, -0.707107f, -0.923880f,
  -1.000000f, -0.923880f, -0.707107f, -0.382683f,
  0.000000f, 0.382683f, 0.707107f, 0.923880f,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
};

volatile Buffer(Q4.20) fftReal4[32] = {
  1.0f, 0.7071f, 0.0f, -0.7071f,
  -1.0f, -0.7071f, 0.0f, 0.7071f,
  1.0f, 0.7071f, 0.0f, -0.7071f,
  -1.0f, -0.7071f, 0.0f, 0.7071f,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
};

volatile Buffer(Q4.20) fftReal5[32] = {
  1.0f, -1.0f, 1.0f, -1.0f,
  1.0f, -1.0f, 1.0f, -1.0f,
  1.0f, -1.0f, 1.0f, -1.0f,
  1.0f, -1.0f, 1.0f, -1.0f,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
};

volatile Buffer(Q4.20) fftReal6[32] = {
  0.000000f, 0.382683f, 0.707107f, 0.923880f,
  1.000000f, 0.923880f, 0.707107f, 0.382683f,
  0.000000f, -0.382683f, -0.707107f, -0.923880f,
  -1.000000f, -0.923880f, -0.707107f, -0.382683f,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
};

volatile Buffer(Q4.20) fftReal7[32] = {
  2.000000f, 1.306563f, 0.000000f, -0.541196f,
  0.000000f, 0.541196f, 0.000000f, -1.306563f,
  -2.000000f, -1.306563f, 0.000000f, 0.541196f,
  0.000000f, -0.541196f, 0.000000f, 1.306563f,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
};

volatile Buffer(Q4.20) fftImag[32] = {
  0.0f, 0.0f, 0.0f, 0.0f,
  0.0f, 0.0f, 0.0f, 0.0f,
  0.0f, 0.0f, 0.0f, 0.0f,
  0.0f, 0.0f, 0.0f, 0.0f,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
};

volatile Buffer(Q4.20) fftStageReal[32];

volatile Buffer(Q4.20) fftStageImag[32];
