// Seeded violation: the deprecated throw() exception specification.
#include <cstdint>

namespace kv::rule_4_1_2_throw_spec::bad {

std::uint32_t id(std::uint32_t v) throw();  // seeded
std::uint32_t id(std::uint32_t v) throw() { return v; }  // seeded

}  // namespace kv::rule_4_1_2_throw_spec::bad
