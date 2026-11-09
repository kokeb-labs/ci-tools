// Seeded violation: a class derived from the deprecated std::iterator.
#include <iterator>
#include <cstdint>

namespace kv::rule_4_1_2_iterator_base::bad {

struct Counting : std::iterator<std::input_iterator_tag, std::uint32_t> {
  std::uint32_t n{0U};
};

std::uint32_t start(const Counting& c) { return c.n; }

}  // namespace kv::rule_4_1_2_iterator_base::bad
