// Compliant: the definition includes the header that declares it.
#include "ok_api.hpp"

namespace kv::rule_6_5_1::ok {

std::int32_t exported_sum(std::int32_t a, std::int32_t b) { return (a == b) ? a : b; }

}  // namespace kv::rule_6_5_1::ok
