// The same function in an .ipp file (a header-only implementation), which must be measured too.
// Deliberately over the complexity limits: the host-quality self-test expects lizard to report it.
inline int classify_template(int a, int b, int c, int d, int e, int f, int g, int h) {
  int r = 0;
  if (a > 0) { r += 1; }
  if (b > 0) { r += 2; }
  if (c > 0) { r += 3; }
  if (d > 0) { r += 4; }
  if (e > 0) { r += 5; }
  if (f > 0) { r += 6; }
  if (g > 0) { r += 7; }
  if (h > 0) { r += 8; }
  if (a > b && c > d) { r *= 2; }
  if (e > f || g > h) { r *= 3; }
  for (int i = 0; i < a; ++i) { if (i % 2 == 0) { r += i; } else if (i % 3 == 0) { r -= i; } }
  while (r > 1000) { r /= 2; }
  return r > 0 ? r : -r;
}
