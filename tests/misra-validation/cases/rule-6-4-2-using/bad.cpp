// Seeded violation: an overload declared after the using-declaration is not found through it.
#include <cstdint>

namespace kv::rule_6_4_2_using::bad {

namespace lib {
std::int32_t convert(std::int32_t v);
}  // namespace lib

using lib::convert;

namespace lib {
std::int32_t convert(std::int64_t v);
}  // namespace lib

std::int32_t use() { return convert(std::int64_t{5}); }

}  // namespace kv::rule_6_4_2_using::bad
