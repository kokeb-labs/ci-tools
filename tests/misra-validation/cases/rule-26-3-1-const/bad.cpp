// Seeded violation: std::vector<bool> as a const object and as a reference parameter.
#include <cstddef>
#include <vector>

namespace kv::rule_26_3_1_const::bad {

std::size_t count_flags(const std::vector<bool>& flags) { return flags.size(); }

std::size_t make_and_count() {
  const std::vector<bool> flags(4U, true);
  return count_flags(flags);
}

}  // namespace kv::rule_26_3_1_const::bad
