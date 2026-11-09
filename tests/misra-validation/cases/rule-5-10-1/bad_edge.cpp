// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_5_10_1::bad_edge {

std::uint32_t split__name(std::uint32_t v) { return v; }  // double underscore inside
struct Reg {
  std::uint32_t _Field{0U};  // leading underscore and capital
};
std::uint32_t field(const Reg& r) { return r._Field; }

}  // namespace kv::rule_5_10_1::bad_edge
