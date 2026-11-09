// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_4_1_2_throw_spec::bad_edge {

struct Codec {
  std::uint32_t decode(std::uint32_t v) const throw() { return v; }
};
std::uint32_t use(const Codec& c) { return c.decode(1U); }

}  // namespace kv::rule_4_1_2_throw_spec::bad_edge
