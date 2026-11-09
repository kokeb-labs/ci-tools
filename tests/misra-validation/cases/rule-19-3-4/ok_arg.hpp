// Near miss: a parameter used as a function argument.
#ifndef KV_RULE_19_3_4_OK_ARG_HPP
#define KV_RULE_19_3_4_OK_ARG_HPP

#include <cstdint>

namespace kv::rule_19_3_4::ok_arg {

[[nodiscard]] inline std::uint32_t twice(std::uint32_t v) { return v * 2U; }

}  // namespace kv::rule_19_3_4::ok_arg

#define KV_RULE_19_3_4_CALL(X) kv::rule_19_3_4::ok_arg::twice(X)

namespace kv::rule_19_3_4::ok_arg {

inline std::uint32_t call(std::uint32_t a, std::uint32_t b) { return KV_RULE_19_3_4_CALL(a + b); }

}  // namespace kv::rule_19_3_4::ok_arg

#undef KV_RULE_19_3_4_CALL

#endif  // KV_RULE_19_3_4_OK_ARG_HPP
