// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_6_2_2_OBJECT_OK_NEAR_HPP
#define KV_RULE_6_2_2_OBJECT_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_6_2_2_object::near {

// Objects with the same name in different namespaces are different entities.
namespace a {
inline constexpr std::int32_t kThreshold{5};
}  // namespace a
namespace b {
inline constexpr std::int64_t kThreshold{6};
}  // namespace b
inline std::int64_t sum() { return static_cast<std::int64_t>(a::kThreshold) + b::kThreshold; }

}  // namespace kv::rule_6_2_2_object::near

#endif  // KV_RULE_6_2_2_OBJECT_OK_NEAR_HPP
