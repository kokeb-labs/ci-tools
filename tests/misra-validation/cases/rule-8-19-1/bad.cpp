// Seeded violation: the comma operator sequences two actions in one expression.
#include <cstdint>

namespace kv::rule_8_19_1::bad {

std::uint32_t step(std::uint32_t& a, std::uint32_t& b) {
  return (++a, ++b);  // seeded
}

}  // namespace kv::rule_8_19_1::bad
