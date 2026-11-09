// Seeded violation: a lambda kept in a variable captures a local implicitly.
#include <cstdint>

namespace kv::rule_8_1_2::bad {

std::uint32_t read(std::uint32_t start) {
  std::uint32_t base = start;
  auto f = [=]() { return base; };  // seeded
  return f();
}

}  // namespace kv::rule_8_1_2::bad
