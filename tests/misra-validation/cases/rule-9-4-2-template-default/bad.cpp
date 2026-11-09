// Seeded violation of the claimed query (from the main case), so the case also proves detection.
#include <cstdint>

namespace kv::rule_9_4_2_template_default::bad {

std::int32_t weight(std::int32_t code) {
  std::int32_t w = 0;
  switch (code) {  // seeded
    case 1:
      w = 5;
    case 2:
      w += 7;
      break;
  }
  return w;
}

}  // namespace kv::rule_9_4_2_template_default::bad
