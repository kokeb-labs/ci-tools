// Seeded violation: the non-member std::empty discarded, and std::remove discarded through a cast to void
// (a cast to void is not a use).
#include <algorithm>
#include <array>
#include <cstdint>
#include <iterator>

namespace kv::rule_28_6_4::bad_nonmember {

void probe(const std::array<std::int32_t, 4U>& values) { std::empty(values); }  // seeded

void tidy(std::array<std::int32_t, 4U>& values) {
  static_cast<void>(std::remove(values.begin(), values.end(), 0));  // seeded
}

}  // namespace kv::rule_28_6_4::bad_nonmember
