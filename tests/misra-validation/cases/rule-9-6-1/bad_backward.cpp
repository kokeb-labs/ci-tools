// Seeded violation (backward): a backward goto forming a retry loop.
#include <cstdint>

namespace kv::rule_9_6_1::bad_backward {

std::int32_t retry(std::int32_t tries) {
  std::int32_t left = tries;
again:
  if (left > 0) {
    --left;
    goto again;
  }
  return left;
}

}  // namespace kv::rule_9_6_1::bad_backward
