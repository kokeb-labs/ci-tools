// Seeded violation (nodefault): a switch whose clauses all end in break, but with no default label.
#include <cstdint>

namespace kv::rule_9_4_2::bad_nodefault {

std::int32_t weight(std::int32_t code) {
  std::int32_t w = 0;
  switch (code) {  // seeded
    case 1:
      w = 5;
      break;
    case 2:
      w = 7;
      break;
  }
  return w;
}

}  // namespace kv::rule_9_4_2::bad_nodefault
