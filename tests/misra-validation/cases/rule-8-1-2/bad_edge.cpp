// Edge cases of the seeded violation.
#include <cstdint>

namespace kv::rule_8_1_2::bad_edge {

std::uint32_t by_reference(std::uint32_t start) {
  std::uint32_t base = start;
  auto f = [&]() { return base; };  // seeded
  return f();
}

std::uint32_t mixed(std::uint32_t start, std::uint32_t step) {
  std::uint32_t base = start;
  auto f = [=, &step]() { return base + step; };  // seeded
  return f();
}

}  // namespace kv::rule_8_1_2::bad_edge
