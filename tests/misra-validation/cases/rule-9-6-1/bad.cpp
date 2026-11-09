// Seeded violation: a forward goto to leave a loop early.
#include <cstdint>

namespace kv::rule_9_6_1::bad {

std::int32_t first_negative(const std::int32_t* values, std::int32_t n) {
  std::int32_t found = -1;
  for (std::int32_t i = 0; i < n; ++i) {
    if (values[i] < 0) {
      found = i;
      goto done;
    }
  }
done:
  return found;
}

}  // namespace kv::rule_9_6_1::bad
