// Seeded violation: an object read after it has been moved from.
#include <cstddef>
#include <string>
#include <utility>

namespace kv::rule_28_6_3::bad {

std::size_t total_length() {
  std::string first{"sensor"};
  const std::string second = std::move(first);
  return first.size() + second.size();  // seeded
}

}  // namespace kv::rule_28_6_3::bad
