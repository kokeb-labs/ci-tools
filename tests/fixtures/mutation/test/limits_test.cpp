#include <cstdio>

#include "limits.hpp"

#define EXPECT(cond)                         \
  do {                                       \
    if (!(cond)) {                           \
      std::printf("failed: %s\n", #cond);    \
      return 1;                              \
    }                                        \
  } while (false)

int main() {
  EXPECT(fixture::Clamp(-5, 0, 10) == 0);
  EXPECT(fixture::Clamp(-1, 0, 10) == 0);
  EXPECT(fixture::Clamp(15, 0, 10) == 10);
  EXPECT(fixture::Clamp(7, 0, 10) == 7);
  int count = 0;
  while (fixture::Step(count)) {
  }
  EXPECT(count == 100);
  EXPECT(!fixture::Step(count));
  return 0;
}
