// Edge cases: more forms of the violation.
#include <cstdint>
#include <iterator>

namespace kv::rule_4_1_2_iterator_base_template::bad {

template <typename T>
struct Walker : std::iterator<std::forward_iterator_tag, T> {  // seeded
  T pos{};
};
std::uint32_t at(const Walker<std::uint32_t>& w) { return w.pos; }

}  // namespace kv::rule_4_1_2_iterator_base_template::bad
