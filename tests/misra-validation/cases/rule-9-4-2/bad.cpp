// Seeded violation: a switch with fall-through between clauses and no default.
#include <cstdint>

namespace kv::rule_9_4_2::bad {

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

}  // namespace kv::rule_9_4_2::bad
