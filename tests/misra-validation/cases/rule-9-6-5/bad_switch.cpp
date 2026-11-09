// Seeded violation (switch): a switch that returns in each case but has no default and nothing after it.
#include <cstdint>

namespace kv::rule_9_6_5::bad_switch {

std::int32_t code_of(std::int32_t k) {
  switch (k) {
    case 0:
      return 10;
    case 1:
      return 20;
  }
}  // seeded

}  // namespace kv::rule_9_6_5::bad_switch
