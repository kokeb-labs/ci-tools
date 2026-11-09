// Seeded violation: an lvalue reference parameter left in a potentially moved-from state when the function returns.
#include <cstddef>
#include <string>
#include <utility>

namespace kv::rule_28_6_3::bad_ref_param {

std::size_t take(std::string& name) {
  const std::string kept{std::move(name)};  // seeded
  return kept.size();
}

}  // namespace kv::rule_28_6_3::bad_ref_param
