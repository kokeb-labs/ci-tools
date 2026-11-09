// Seeded violation (split): the #if group opened here is meant to be closed by the #endif in an included file.
#if !defined(KV_FEATURE)  // seeded
#include "kv_close.inc"
namespace kv::rule_19_1_2::bad_split {
constexpr int kValue = 1;
}
