// Seeded violation (switch): a goto that leaves a switch inside a loop.
#include <cstdint>

namespace kv::rule_9_6_1::bad_switch {

std::int32_t scan(const std::int32_t* codes, std::int32_t n) {
  std::int32_t i = 0;
  for (; i < n; ++i) {
    switch (codes[i]) {
      case 0:
        goto out;  // seeded
      default:
        break;
    }
  }
out:
  return i;
}

}  // namespace kv::rule_9_6_1::bad_switch
