// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_4_1_2_ITERATOR_BASE_TEMPLATE_OK_HPP
#define KV_RULE_4_1_2_ITERATOR_BASE_TEMPLATE_OK_HPP

#include <cstddef>
#include <cstdint>
#include <iterator>

namespace kv::rule_4_1_2_iterator_base_template::ok {

// An iterator that declares its member types itself instead of inheriting std::iterator.
struct Counting {
  using iterator_category = std::input_iterator_tag;
  using value_type = std::uint32_t;
  using difference_type = std::ptrdiff_t;
  using pointer = const std::uint32_t*;
  using reference = const std::uint32_t&;
  std::uint32_t n{0U};
};
inline std::uint32_t start(const Counting& c) { return c.n; }

}  // namespace kv::rule_4_1_2_iterator_base_template::ok

#endif  // KV_RULE_4_1_2_ITERATOR_BASE_TEMPLATE_OK_HPP
