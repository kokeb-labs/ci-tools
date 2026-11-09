// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_6_0_3_OK_NEAR_HPP
#define KV_RULE_6_0_3_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_6_0_3::near {

// An enumeration, an alias and a namespace alias, all inside a named namespace.
enum class Mode : std::uint8_t { kIdle, kRun };
using Raw = std::uint32_t;
namespace self = kv::rule_6_0_3::near;
inline Raw mode_raw(self::Mode m) { return static_cast<Raw>(m); }

}  // namespace kv::rule_6_0_3::near

#endif  // KV_RULE_6_0_3_OK_NEAR_HPP
