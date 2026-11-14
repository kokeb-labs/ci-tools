#include <cstdio>
#include <cstring>

#include "ring/ring.hpp"

int main() {
  ring::Ring r;
  for (unsigned i = 0U; i < ring::Ring::kCapacity; ++i) {
    if (!r.Push(static_cast<std::uint8_t>(i))) {
      std::puts("push failed before capacity");
      return 1;
    }
  }
  if (r.Push(99U)) {
    std::puts("push beyond capacity accepted");
    return 1;
  }
  std::uint8_t v = 0U;
  if (!r.Pop(v) || (v != 0U) || (r.Size() != ring::Ring::kCapacity - 1U)) {
    std::puts("pop order or size wrong");
    return 1;
  }
  std::printf("ring ok (%s)\n", ring::Configuration());
  return 0;
}
