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
