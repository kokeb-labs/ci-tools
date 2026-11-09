// Seeded violation: a scoped enumeration with explicit enumerator values and no fixed underlying type.
namespace kv::rule_10_2_1::bad {

enum class Mode { kIdle = 0, kRun = 1 };  // seeded

Mode next(Mode m) { return (m == Mode::kIdle) ? Mode::kRun : Mode::kIdle; }

}  // namespace kv::rule_10_2_1::bad
