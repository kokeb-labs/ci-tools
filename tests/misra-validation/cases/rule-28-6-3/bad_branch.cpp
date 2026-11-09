// Seeded violation: moved from on one path, then read after the paths join.
#include <cstddef>
#include <string>
#include <utility>

namespace kv::rule_28_6_3::bad_branch {

std::size_t keep_or_give(bool give, std::string& out) {
  std::string name{"probe"};
  if (give) {
    out = std::move(name);
  }
  return name.size();  // seeded
}

}  // namespace kv::rule_28_6_3::bad_branch
