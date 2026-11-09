// Seeded violation: a function declared noexcept throws.
namespace kv::rule_18_5_1::bad {

void stop() noexcept { throw 1; }  // seeded

}  // namespace kv::rule_18_5_1::bad
