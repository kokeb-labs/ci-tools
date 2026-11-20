// C++20 features present in both GCC 10 and Clang 13 with libstdc++ 10: concepts, <span>, <bit>.
#include <array>
#include <bit>
#include <concepts>
#include <cstdint>
#include <span>

template <std::unsigned_integral T>
constexpr int Ones(T v) {
  return std::popcount(v);
}

int main() {
  const std::array<std::uint8_t, 3> data{1, 3, 7};
  const std::span<const std::uint8_t> view{data};
  int total = 0;
  for (const auto b : view) {
    total += Ones(b);
  }
  return total == 6 ? 0 : 1;
}
