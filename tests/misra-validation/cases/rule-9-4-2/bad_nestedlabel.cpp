// Seeded violation (nestedlabel): a case label inside a nested block of the switch body.
#include <cstdint>

namespace kv::rule_9_4_2::bad_nestedlabel {

std::int32_t odd(std::int32_t code, bool flag) {
  std::int32_t w = 0;
  switch (code) {
    case 1:
      if (flag) {
        case 2:
          w = 2;
      }
      break;
    default:
      break;
  }
  return w;
}

}  // namespace kv::rule_9_4_2::bad_nestedlabel
