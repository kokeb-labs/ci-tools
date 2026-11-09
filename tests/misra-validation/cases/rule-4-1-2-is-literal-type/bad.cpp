// Seeded violation: the deprecated std::is_literal_type trait.
#include <type_traits>
#include <cstdint>

namespace kv::rule_4_1_2_is_literal_type::bad {

bool literal() { return std::is_literal_type<std::uint32_t>::value; }  // seeded

}  // namespace kv::rule_4_1_2_is_literal_type::bad
