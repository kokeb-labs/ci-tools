// Seeded violation: the packed std::vector<bool> specialisation.
#include <cstddef>
#include <vector>

namespace kv::rule_26_3_1::bad {

std::size_t count_flags() {
  std::vector<bool> flags(8U, false);  // seeded
  flags[0] = true;
  return flags.size();
}

}  // namespace kv::rule_26_3_1::bad
