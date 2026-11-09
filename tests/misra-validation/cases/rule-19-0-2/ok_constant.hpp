// Near miss: an object-like macro defining a constant is not a function-like macro.
#ifndef KV_RULE_19_0_2_OK_CONSTANT_HPP
#define KV_RULE_19_0_2_OK_CONSTANT_HPP

#include <cstdint>

#define KV_RULE_19_0_2_CONFIG 3U

namespace kv::rule_19_0_2::ok_constant {

[[nodiscard]] inline std::uint32_t config() { return KV_RULE_19_0_2_CONFIG; }

}  // namespace kv::rule_19_0_2::ok_constant

#undef KV_RULE_19_0_2_CONFIG

#endif  // KV_RULE_19_0_2_OK_CONSTANT_HPP
