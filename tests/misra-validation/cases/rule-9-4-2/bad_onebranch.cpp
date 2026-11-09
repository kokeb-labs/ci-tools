// Seeded violation (onebranch): a switch with only one branch.
#include <cstdint>

namespace kv::rule_9_4_2::bad_onebranch {

std::int32_t only(std::int32_t code) {
  std::int32_t w = 0;
  switch (code) {  // seeded
    default:
      w = 1;
      break;
  }
  return w;
}

}  // namespace kv::rule_9_4_2::bad_onebranch
