// Seeded violation (forinit): two declarators in a for-init and two in a member declaration.
#include <cstdint>

namespace kv::rule_10_0_1::bad_forinit {

struct Span {
  std::int32_t lo, hi;  // seeded
};

std::int32_t width(const Span& s) {
  std::int32_t w = 0;
  for (std::int32_t i = s.lo, j = s.hi; i < j; ++i) {  // seeded
    ++w;
  }
  return w;
}

}  // namespace kv::rule_10_0_1::bad_forinit
