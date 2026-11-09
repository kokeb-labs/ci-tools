// Near misses (transfer): a function name and a captureless lambda passed by value to a parameter of
// pointer-to-function type. Passing an argument is a converting transfer to an object of that type, which the
// guideline accepts as an appropriate context.
#ifndef KV_RULE_7_11_3_OK_TRANSFER_HPP
#define KV_RULE_7_11_3_OK_TRANSFER_HPP

#include <cstdint>

namespace kv::rule_7_11_3::ok_transfer {

inline std::int32_t two() { return 2; }

using Fn = std::int32_t (*)();

inline std::int32_t call(Fn f) { return f(); }

inline std::int32_t by_name() { return call(two); }

inline std::int32_t by_lambda() { return call([]() -> std::int32_t { return 3; }); }

}  // namespace kv::rule_7_11_3::ok_transfer

#endif  // KV_RULE_7_11_3_OK_TRANSFER_HPP
