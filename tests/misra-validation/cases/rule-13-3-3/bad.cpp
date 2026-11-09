// Seeded violation: a declaration and the definition name the same parameter differently.
#include <cstdint>

namespace kv::rule_13_3_3::bad {

std::int32_t clamp_to(std::int32_t value, std::int32_t limit);

std::int32_t clamp_to(std::int32_t limit, std::int32_t value) {  // seeded
  return (value > limit) ? limit : value;
}

}  // namespace kv::rule_13_3_3::bad
