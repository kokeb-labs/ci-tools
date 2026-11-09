// Seeded violation: the value of an assignment is used inside a condition.
#include <cstdint>

namespace kv::rule_8_18_2::bad {

bool latch(std::uint32_t& stored, std::uint32_t next) {
  if ((stored = next) != 0U) {
    return true;
  }
  return false;
}

}  // namespace kv::rule_8_18_2::bad
