// Seeded violation: the moved-from string is read before it is given a new value.
#include <cstddef>
#include <string>
#include <utility>

namespace kv::rule_28_6_3_reassigned::bad {

std::size_t total_length() {
  std::string first{"sensor"};
  const std::string second = std::move(first);
  const std::size_t stale = first.size();
  first = "probe";
  return stale + second.size();
}

}  // namespace kv::rule_28_6_3_reassigned::bad
